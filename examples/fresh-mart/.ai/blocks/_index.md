# 积木索引

本文件是所有业务流程积木的目录，按业务域分类。

## 会员

- [会员注册](member_register.md) — 小程序新用户注册并发放新人券
- [会员等级升级](member_level_upgrade.md) — 积分变动后自动判断等级升级

## 商品

- [商品浏览](product_browse.md) — 商品列表与详情聚合（含活动 + 我的可用券）

## 营销

- [创建优惠券模板](coupon_create.md) — 运营后台创建券模板
- [用户领券](coupon_receive.md) — 小程序领取优惠券（防超发 + 限领）

## 订单 ⭐ 核心复杂流程

- [创建订单](order_create.md) — 跨 5 服务的下单流程，含 try-compensate
- [订单支付](order_pay.md) — 发起支付 + 微信回调（8 步关键链路）
- [订单退款](order_refund.md) — 跨 5 服务的退款编排（最复杂）

---

**维护规则**：

- 新增积木时用 `vibe-blocks new <id> --group <分组>` 自动注册
- 复杂积木标 ⭐ 标签便于识别
- 状态：✅ stable / 🟡 draft / ⚠️ deprecated
