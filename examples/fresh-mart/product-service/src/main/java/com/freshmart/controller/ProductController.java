// === 伪代码 === //
package com.freshmart.product.controller;

@RestController
@RequestMapping("/v1/product")
class ProductController {

    @Resource ProductService productService;

    @GetMapping("/list")
    BaseResponse<Page<ProductDTO>> list(ProductQuery q) {
        return BaseResponse.ok(productService.queryPage(q));
    }

    @GetMapping("/{productId}")
    BaseResponse<ProductDTO> detail(@PathVariable Long productId) {
        return BaseResponse.ok(productService.findById(productId));
    }

    /** 批量查询商品 — order-service 下单时调用 */
    @PostMapping("/batch")
    BaseResponse<List<ProductDTO>> batchGet(@RequestBody List<Long> ids) {
        return BaseResponse.ok(productService.findByIds(ids));
    }

    /** 锁定库存（下单时） — 见积木 order_create step 4 */
    @PostMapping("/stock/lock")
    BaseResponse<Void> lockStock(@RequestBody LockStockRequest req) {
        productService.lockStock(req.items, req.orderNo);
        return BaseResponse.ok();
    }

    /** 释放库存（下单失败、超时未支付）— 见积木 order_create / order_pay 异常路径 */
    @PostMapping("/stock/release")
    BaseResponse<Void> releaseStock(@RequestBody ReleaseStockRequest req) {
        productService.releaseStock(req.orderNo);
        return BaseResponse.ok();
    }

    /** 扣减库存（支付成功后）— 见积木 order_pay step 4 */
    @PostMapping("/stock/deduct")
    BaseResponse<Void> deductStock(@RequestBody DeductStockRequest req) {
        productService.deductStock(req.orderNo);
        return BaseResponse.ok();
    }

    /** 退回库存（退款）— 见积木 order_refund step 5 */
    @PostMapping("/stock/refund")
    BaseResponse<Void> refundStock(@RequestBody RefundStockRequest req) {
        productService.refundStock(req.orderNo);
        return BaseResponse.ok();
    }
}
