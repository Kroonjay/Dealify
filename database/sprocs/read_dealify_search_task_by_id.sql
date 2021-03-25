DELIMITER //
CREATE PROCEDURE ReadDealifySearchTaskById (
    IN task_id_param INT
) BEGIN
SELECT task_id, task_name, task_type, task_status, task_config, created_at, last_execution_at FROM DealifySearchTasks WHERE task_id = task_id_param LIMIT 1;
END //