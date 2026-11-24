# MR_Textility — UE 5.7 版本

这是 MR_Textility（原 UE 5.8 项目，仓库 BBandeng/MR_Textility）迁移到 **Unreal Engine 5.7** 的版本。

- 打开方式：用 UE 5.7 打开 `MRPARADISE.uproject`
- 关卡：`Level1Heaven`、`Level1Heaven_RealClouds`、`Level2_CloudReveal`（与原项目结构相同）
- 出场效果：`BPC_FlyIn` 组件（按 3 / 4 键），`Level1Heaven_RealClouds` 关卡蓝图（按 1 / 2 键：云层聚拢、光照渐变）
- 序列：`LS_Level1Heaven`、`LS_Intro`、`Level1Heaven/LS_Level1Heaven_RealClouds`、`LS_CloudReveal`

## 未包含在仓库中

- `Content/Clouds_Tunnel_Loop/`（Fab 云隧道 VDB 素材包，约 13.6 GB）：三个关卡都没有用到，为节省 Git LFS 额度没有上传。需要时可从 Fab 重新添加到项目。
- `DerivedDataCache/`、`Intermediate/`、`Saved/`：引擎缓存，首次打开会自动生成。

## 克隆

本仓库使用 Git LFS，克隆前请先安装 Git LFS（GitHub Desktop 自带）。
