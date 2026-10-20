# wabi-workspace

仓库所有者用于保存 Wabi 协助编写的通用脚本、配置示例与说明的公开仓库。

这不是 Wabi 自身的运行环境，也不是 Wabi 的持久记忆。仓库不会自动同步聊天、邮箱或其他个人资料。提交前请自行检查文件中没有密码、令牌、个人资料或真实服务配置。

## 示例：检查 YAML 语法

`check_yaml.py` 只读取指定的本地 UTF-8 文件，使用 PyYAML 的安全加载器检查一个或多个 YAML 文档能否解析，不修改文件、不发起网络请求，也不执行配置中的命令。

需要 Python 3.10 或更新版本。推荐在虚拟环境安装依赖（Windows 可使用 `py`，并改用 `.venv\Scripts\python`）：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/check_yaml.py examples/config.yaml
```

也可一次检查多个文件：

```sh
.venv/bin/python scripts/check_yaml.py first.yaml second.yml
```

- 全部文件能解析时退出码为 `0`。
- 存在语法、编码或文件读取错误时退出码为 `1`；仍会继续检查其余文件。
- 没有传入文件时显示用法，退出码为 `2`。

这是语法示例，不是完整的配置验证器：不会验证业务字段、应用兼容性、重复键或连接是否可用。不要把“能解析”当作“可部署”。请仅检查可信来源、大小合理的本地文件。

## 范围

当前没有自动部署、GitHub Actions 工作流或外部服务集成。示例中的名称和数值均为虚构，不含真实节点、账号或凭据。
