DELIMITER //
CREATE PROCEDURE ReadDealifyTaskIdsByTypes (
    IN task_type_param NVARCHAR(255)
) BEGIN
SELECT task_id FROM DealifySearchTasks WHERE task_type IN task_type_param AND task_status = 0;
END //