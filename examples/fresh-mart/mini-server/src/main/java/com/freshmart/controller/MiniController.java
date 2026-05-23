// === 伪代码 === //
// C 端小程序 BFF：聚合 member/product/promotion/order 服务给前端用。
package com.freshmart.mini.controller;

@RestController
@RequestMapping("/api/mini")
class MiniController {

    @Resource MemberClient memberClient;
    @Resource ProductClient productClient;
    @Resource PromotionClient promotionClient;
    @Resource OrderClient orderClient;

    /** 注册 — 见积木 member_register */
    @PostMapping("/register")
    BaseResponse<Long> register(@RequestBody RegisterRequest req) {
        return memberClient.register(req);
    }

    /** 商品列表 — 见积木 product_browse */
    @GetMapping("/products")
    BaseResponse<Page<ProductDTO>> products(ProductQuery q) {
        return productClient.list(q);
    }

    /** 商品详情（聚合：商品基础信息 + 当前活动 + 用户已领的可用券） */
    @GetMapping("/product/{productId}")
    BaseResponse<ProductDetailVO> productDetail(
            @PathVariable Long productId,
            @RequestHeader("X-Member-Id") Long memberId) {
        ProductDTO product = checkResponse(productClient.detail(productId));
        List<ActivityDTO> activities = promotionClient.activitiesByProduct(productId).getData();
        List<CouponDTO> myCoupons = promotionClient.myAvailableCoupons(memberId).getData();
        return BaseResponse.ok(ProductDetailVO.of(product, activities, myCoupons));
    }

    /** 领券 — 见积木 coupon_receive */
    @PostMapping("/coupon/receive")
    BaseResponse<Long> receiveCoupon(@RequestBody ReceiveCouponRequest req) {
        return promotionClient.receive(req);
    }

    /** 下单 — 见积木 order_create */
    @PostMapping("/order")
    BaseResponse<OrderDTO> createOrder(@RequestBody CreateOrderRequest req) {
        return orderClient.create(req);
    }

    /** 发起支付 — 见积木 order_pay */
    @PostMapping("/order/pay")
    BaseResponse<PayDTO> pay(@RequestBody PayRequest req) {
        return orderClient.pay(req);
    }
}
