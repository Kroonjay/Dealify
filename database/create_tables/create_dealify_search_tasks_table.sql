CREATE TABLE DealifySearchTasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    task_name NVARCHAR(90) NOT NULL,
    task_type INT NOT NULL,
    task_status INT NOT NULL DEFAULT 0,
    task_config JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_execution_at DATETIME NOT NULL DEFAULT '2000-04-20 07:10:00'
);