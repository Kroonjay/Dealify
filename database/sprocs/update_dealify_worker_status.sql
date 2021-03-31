DELIMITER //
CREATE PROCEDURE UpdateDealifyWorkerStatus (
    IN worker_id_param INT,
    IN worker_status_param INT
)
BEGIN
UPDATE DealifyWorkers SET worker_status = worker_status_param WHERE worker_id = worker_id_param LIMIT 1;
SELECT worker_status FROM DealifyWorkers WHERE worker_id = worker_id_param LIMIT 1;
END //