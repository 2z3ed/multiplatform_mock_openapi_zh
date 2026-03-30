INSERT INTO training_case (conversation_id, customer_id, case_title, case_summary, case_type, source_json) VALUES
(NULL, NULL, '高效处理客户投诉案例', '客服快速响应并解决客户物流延误投诉，客户满意度高', 'good', '{"resolution_time": "5min", "satisfaction_score": 5}'),
(NULL, NULL, '退换货处理不当案例', '客服未能及时处理退换货请求，导致客户投诉升级', 'bad', '{"resolution_time": "2days", "satisfaction_score": 2}'),
(NULL, NULL, '典型产品咨询场景', '客户咨询产品功能，客服提供详细解答', 'typical', '{"category": "product_inquiry"}'),
(NULL, NULL, '突发系统故障应对', '系统故障期间客服手动记录客户需求并后续跟进', 'edge_case', '{"incident": "system_outage", "manual_workaround": true}'),
(NULL, NULL, 'VIP客户专属服务', 'VIP客户享受专属客服通道，响应时间优先', 'good', '{"vip_level": "gold", "priority": "high"}');
