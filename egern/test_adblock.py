"""Offline regression tests, NOT the Egern runtime. SPDX-License-Identifier: GPL-3.0-only."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import yaml
from build_adblock import render

ROOT = Path(__file__).resolve().parent
class UniqueKeyLoader(yaml.SafeLoader):
    pass

def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result
UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

def matches(entry, host):
    value = entry['match']
    return host == value or (entry['kind'] == 'domain_suffix' and host.endswith('.' + value))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream-hosts', type=Path, help='Optional pinned StevenBlack hosts snapshot')
    parser.add_argument('--hagezi-domains', type=Path, help='Optional pinned HaGeZi LIGHT domain snapshot')
    args = parser.parse_args()
    text = (ROOT / 'adblock-lite.yaml').read_text(encoding='utf-8')
    source = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
    entries = source['entries']
    assert render() == text, 'Module differs from reproducible build'
    module = yaml.load(text, Loader=UniqueKeyLoader)
    assert set(module) == {'name','description','author','homepage','manual','rules'}
    assert all(isinstance(module[k], str) and module[k] for k in set(module)-{'rules'})
    assert len(entries) == len(module['rules']) == 396
    assert len({(e['kind'], e['match']) for e in entries}) == len(entries)
    scopes = [s for group in source['platform_scopes'].values() for s in group]
    for item, entry in zip(module['rules'], entries):
        assert set(item) == {entry['kind']} and entry['kind'] in {'domain','domain_suffix'}
        rule = item[entry['kind']]
        assert set(rule) == {'match','policy','name'} and rule['policy'] == 'REJECT'
        assert rule['match'] == entry['match'] and rule['name'].startswith('Wabi广告 · ')
        assert re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z]{2,}', entry['match'])
        assert entry['source'] in source['sources']
        assert entry['kind'] == ('domain_suffix' if entry['source']=='hagezi-light' else 'domain')
        assert entry['match'] in source['v1_domains'] or any(entry['match']==s or entry['match'].endswith('.'+s) for s in scopes)
    forbidden = {'qq.com','baidu.com','google.com','googleapis.com','googlevideo.com','apple.com','icloud.com','alipay.com','taobao.com','alicdn.com','tencent.com','xiaomi.com','unity3d.com','x.com','twitter.com','byteimg.com','snssdk.com','bcebos.com','pinduoduo.com','mob.com','jiguang.cn','jpush.cn','jpush.io','getui.com','getui.net','igexin.com','umeng.com','amplitude.com','adjust.com'}
    assert not ({e['match'] for e in entries} & forbidden)
    suffix = [e for e in entries if e['kind']=='domain_suffix']
    for entry in entries:
        assert not any(other != entry and matches(other, entry['match']) for other in suffix), 'Redundant covered rule'
    blocked = lambda h: any(matches(e,h) for e in entries)
    cases = 0
    for e in entries:
        host = e['match']
        assert matches(e, host) and blocked(host)
        assert matches(e,'test.'+host) == (e['kind']=='domain_suffix')
        # Test the individual rule's boundaries; a sibling can legitimately match another rule.
        for other in (host+'.example.org', 'not-'+host, host+'evil', host.replace('.','-')):
            assert not matches(e, other)
        cases += 6
    for host in source['v1_domains']:
        assert blocked(host), f'Lost v1 coverage: {host}'
        cases += 1
    controls = [
        'www.qq.com','login.weixin.qq.com','api.weixin.qq.com','wx.qq.com','qzs.qq.com','tpns.qq.com',
        'www.baidu.com','pan.baidu.com','www.alipay.com','mapi.alipay.com','www.taobao.com','acs.m.taobao.com',
        'img.alicdn.com','www.apple.com','api.apple-cloudkit.com','www.icloud.com','api.bilibili.com',
        'www.youtube.com','rr1---sn.example.googlevideo.com','github.com','raw.githubusercontent.com',
        'www.xiaomi.com','api.unity3d.com','unity3d.com','x.com','api.x.com','api.twitter.com','pbs.twimg.com',
        'www.douyin.com','www.kuaishou.com','p3-sign.douyinpic.com','p3-sign.byteimg.com','app.snssdk.com',
        'init.sms.mob.com','sdkapi.sms.mob.com','code.sms.mob.com','sdk.verification.jiguang.cn',
        'smartop-sdkapi.jiguang.cn','api.jpush.cn','sdk.openinstall.io','www.pinduoduo.com','images.pinduoduo.com',
        'video-dsp.pddpic.com','a.adkwai.com.example.org','not-pangle.io','not-googlesyndication.com',
    ]
    for host in controls:
        assert not blocked(host), f'Normal-service control blocked: {host}'
        cases += 1
    positives = ['new.pangle.io','adsmind.gdtimg.com','foo.adkwai.com','mobads.baidu.com','sdkconfig.ad.xiaomi.com','open.e.kuaishou.com','huichuan.sm.cn','adserver.unityads.unity3d.com','ms.applovin.com','cdn.jsdelivr.net.pangle.io']
    for host in positives:
        assert blocked(host), host
        cases += 1
    try:
        yaml.load('a: 1\na: 2\n', Loader=UniqueKeyLoader)
    except ValueError:
        pass
    else:
        raise AssertionError('Duplicate keys accepted')
    print(f'PASS: native structure; reproducible build; {len(entries)} unique rules ({len(suffix)} suffix / {len(entries)-len(suffix)} exact); {cases} matching cases incl. {len(controls)} normal-service controls; no scripts/MITM/DNS/IP/remote dependencies.')
    for key, path in [('stevenblack',args.upstream_hosts),('hagezi-light',args.hagezi_domains)]:
        if path is None:
            continue
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==source['sources'][key]['source_sha256'], f'Wrong {key} snapshot'
        lines = data.decode('utf-8').splitlines()
        if key=='stevenblack':
            members = {p[1] for line in lines if len(p:=line.split())>=2 and p[0] in {'0.0.0.0','127.0.0.1'}}
        else:
            members = {line.strip() for line in lines if line and not line.startswith('#')}
        chosen = [e['match'] for e in entries if e['source']==key]
        assert set(chosen)<=members
        print(f'PASS: {len(chosen)} {key} entries in hash-verified independently licensed source.')
    print('NOT TESTED: Egern device import/kernel/real traffic, actual ad removal, complete app compatibility. Controls establish rule-level nonmatches only.')

if __name__=='__main__':
    main()
