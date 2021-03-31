CREATE TABLE DealifyWorkers (
    worker_id INT AUTO_INCREMENT PRIMARY KEY,
    worker_name NVARCHAR(90) NOT NULL UNIQUE,
    worker_status INT NOT NULL DEFAULT 0,
    current_task INT,
    task_config JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME NOT NULL DEFAULT '2000-04-20 07:10:00',
    CONSTRAINT fkTaskId
    FOREIGN KEY (current_task)
        REFERENCES DealifySearchTasks(task_id)
        ON DELETE SET NULL
)