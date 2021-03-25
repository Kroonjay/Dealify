DELIMITER //
CREATE PROCEDURE StartNextDealifySearchTask ()
BEGIN
SELECT task_id INTO @task_id FROM DealifySearchTasks WHERE task_status = 0 ORDER BY last_execution_at ASC LIMIT 1;
UPDATE DealifySearchTasks SET last_execution_at = CURRENT_TIMESTAMP WHERE task_id = @task_id;
SELECT task_id, task_name, task_type, task_config FROM DealifySearchTasks WHERE task_id = @task_id;
END //