DELIMITER //
CREATE PROCEDURE ReadCraigslistSitesByState (
    IN state_param NVARCHAR(90)
) BEGIN
SELECT * FROM CraigslistSites WHERE state_code LIKE state_param;
END //