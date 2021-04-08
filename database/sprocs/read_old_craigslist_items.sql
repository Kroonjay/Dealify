DELIMITER //
CREATE PROCEDURE ReadOldActiveCraigslistItems (
    IN interval_days_param INT,
    IN limit_param INT
)
BEGIN
SELECT * FROM CraigslistItems WHERE last_seen_at < now() - interval interval_days_param day AND is_deleted = 0 ORDER BY last_seen_at ASC LIMIT limit_param;
END //