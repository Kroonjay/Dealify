DELIMITER //
CREATE PROCEDURE ReadCraigslistSiteIdsByState (
    IN state_param NVARCHAR(90)
) BEGIN
SELECT site_id FROM CraigslistSites WHERE state_code LIKE state_param;
END //