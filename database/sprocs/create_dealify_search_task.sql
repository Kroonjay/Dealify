DELIMITER //
CREATE PROCEDURE CreateDealifySearchTask (
  IN task_name_param NVARCHAR(90),
  IN task_type_param INT,
  IN task_config_param JSON
) BEGIN
INSERT INTO
  DealifySearchTasks (
    task_name,
    task_type,
    task_config
  )
VALUES
  (
    task_name_param,
    task_type_param,
    task_config_param
  );
END //