DELIMITER //
CREATE PROCEDURE ReadDealifyWorkerById(
    IN worker_id_param INT
)
BEGIN
SELECT * FROM DealifyWorkers WHERE worker_id = worker_id_param LIMIT 1;
END //