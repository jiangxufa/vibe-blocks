// === 伪代码 === //
// Feign 客户端定义（每个服务被调用的接口聚合在这里）
package com.freshmart.common.client;

@FeignClient(name = "member-service", path = "/v1/member")
interface MemberClient {
    @PostMapping("/register") BaseResponse<Long> register(@RequestBody RegisterRequest req);
    @GetMapping("/{memberId}") BaseResponse<MemberDTO> get(@PathVariable Long memberId);
    @PostMapping("/points/deduct") BaseResponse<Void> deductPoints(@RequestBody DeductPointsRequest req);
    @PostMapping("/points/add") BaseResponse<Void> addPoints(@RequestBody AddPointsRequest req);
    @PostMapping("/points/refund") BaseResponse<Void> refundPoints(@RequestBody RefundPointsRequest req);
}

@FeignClient(name = "product-service", path = "/v1/product")
interface ProductClient {
    @GetMapping("/list") BaseResponse<Page<ProductDTO>> list(@SpringQueryMap ProductQuery q);
    @GetMapping("/{id}") BaseResponse<ProductDTO> detail(@PathVariable Long id);
    @PostMapping("/batch") BaseResponse<List<ProductDTO>> batchGet(@RequestBody List<Long> ids);
    @PostMapping("/stock/lock") BaseResponse<Void> lockStock(@RequestBody LockStockRequest req);
    @PostMapping("/stock/release") BaseResponse<Void> releaseStock(@RequestBody ReleaseStockRequest req);
    @PostMapping("/stock/deduct") BaseResponse<Void> deductStock(@RequestBody DeductStockRequest req);
    @PostMapping("/stock/refund") BaseResponse<Void> refundStock(@RequestBody RefundStockRequest req);
}

@FeignClient(name = "promotion-service", path = "/v1/promotion")
interface PromotionClient {
    @PostMapping("/coupon/template") BaseResponse<Long> createTemplate(@RequestBody CreateCouponRequest req);
    @PostMapping("/coupon/receive") BaseResponse<Long> receive(@RequestBody ReceiveCouponRequest req);
    @PostMapping("/coupon/lock") BaseResponse<CouponLockResult> lockCoupon(@RequestBody LockCouponRequest req);
    @PostMapping("/coupon/use") BaseResponse<Void> useCoupon(@RequestBody UseCouponRequest req);
    @PostMapping("/coupon/release") BaseResponse<Void> releaseCoupon(@RequestBody String orderNo);
    @PostMapping("/coupon/refund") BaseResponse<Void> refundCoupon(@RequestBody String orderNo);
    @PostMapping("/activity") BaseResponse<Long> createActivity(@RequestBody CreateActivityRequest req);

    @GetMapping("/activities") BaseResponse<List<ActivityDTO>> activitiesByProduct(@RequestParam Long productId);
    @GetMapping("/coupons") BaseResponse<List<CouponDTO>> myAvailableCoupons(@RequestParam Long memberId);
    @GetMapping("/coupons/all") BaseResponse<List<CouponDTO>> couponsByMember(@RequestParam Long memberId);
}

@FeignClient(name = "order-service", path = "/v1/order")
interface OrderClient {
    @PostMapping("/create") BaseResponse<OrderDTO> create(@RequestBody CreateOrderRequest req);
    @PostMapping("/pay") BaseResponse<PayDTO> pay(@RequestBody PayRequest req);
    @PostMapping("/refund") BaseResponse<Void> refund(@RequestBody RefundRequest req);
    @GetMapping("/by-member/{memberId}") BaseResponse<List<OrderDTO>> byMember(@PathVariable Long memberId);
}
