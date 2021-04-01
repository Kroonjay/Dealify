DELIMITER //
CREATE PROCEDURE UpdateDealifyCurrentTaskById (
    IN worker_id_param INT,
    IN current_task_param INT
)
BEGIN
UPDATE DealifyWorkers SET current_task = current_task_param WHERE worker_id = worker_id_param LIMIT 1;
END //