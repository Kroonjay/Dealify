DELIMITER //
CREATE PROCEDURE CreateDealifyWorker(
    IN worker_name_param NVARCHAR(90),
    IN task_config_param JSON
)
BEGIN
INSERT INTO DealifyWorkers (
    worker_name,
    task_config
) VALUES (
    worker_name_param,
    task_config_param
);
END //