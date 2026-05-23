// === 伪代码 === //
package com.freshmart.product.service;

@Service
class ProductService {

    @Resource ProductRepository productRepo;
    @Resource StockRepository stockRepo;
    @Resource StockLockRepository lockRepo;

    Page<ProductDTO> queryPage(ProductQuery q) {
        return productRepo.queryPage(q).map(ProductDTO::from);
    }

    ProductDTO findById(Long productId) {
        return productRepo.findById(productId).map(ProductDTO::from)
                .orElseThrow(() -> new ServiceException("商品不存在"));
    }

    List<ProductDTO> findByIds(List<Long> ids) {
        return productRepo.findAllById(ids).stream()
                .map(ProductDTO::from).collect(toList());
    }

    /** 锁定库存（预扣）— 下单时调用，30 分钟超时自动释放 */
    @Transactional
    void lockStock(List<StockItem> items, String orderNo) {
        for (StockItem item : items) {
            Stock s = stockRepo.findByProductIdForUpdate(item.productId)
                    .orElseThrow(() -> new ServiceException("商品库存不存在"));
            if (s.available < item.qty) {
                throw new ServiceException("商品 " + item.productId + " 库存不足");
            }
            s.available -= item.qty;
            s.locked += item.qty;
            stockRepo.save(s);
            lockRepo.save(new StockLock(orderNo, item.productId, item.qty,
                    LocalDateTime.now().plusMinutes(30)));
        }
    }

    /** 释放预扣库存（订单取消、超时未支付） */
    @Transactional
    void releaseStock(String orderNo) {
        List<StockLock> locks = lockRepo.findByOrderNo(orderNo);
        for (StockLock lock : locks) {
            Stock s = stockRepo.findByProductIdForUpdate(lock.productId)
                    .orElseThrow();
            s.locked -= lock.qty;
            s.available += lock.qty;
            stockRepo.save(s);
        }
        lockRepo.deleteByOrderNo(orderNo);
    }

    /** 真正扣减库存（支付成功后）— locked → 销量 */
    @Transactional
    void deductStock(String orderNo) {
        List<StockLock> locks = lockRepo.findByOrderNo(orderNo);
        for (StockLock lock : locks) {
            Stock s = stockRepo.findByProductIdForUpdate(lock.productId)
                    .orElseThrow();
            s.locked -= lock.qty;
            s.sold += lock.qty;
            stockRepo.save(s);
        }
        lockRepo.deleteByOrderNo(orderNo);
    }

    /** 退款回库存 — 见积木 order_refund step 5 */
    @Transactional
    void refundStock(String orderNo) {
        // 查订单原始商品明细，加回 available
        List<OrderStockSnapshot> snap = lockRepo.findHistoryByOrderNo(orderNo);
        for (OrderStockSnapshot s : snap) {
            Stock stock = stockRepo.findByProductIdForUpdate(s.productId)
                    .orElseThrow();
            stock.available += s.qty;
            stock.sold -= s.qty;
            stockRepo.save(stock);
        }
    }
}
