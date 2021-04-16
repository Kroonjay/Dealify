DELIMITER //
CREATE PROCEDURE ReadCraigslistSitesByCity (
    IN city_param NVARCHAR(90)
) BEGIN
SELECT * FROM CraigslistSites WHERE city LIKE city_param;
END //