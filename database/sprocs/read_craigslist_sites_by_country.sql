DELIMITER //
CREATE PROCEDURE ReadCraigslistSitesByCountry (
    IN country_param NVARCHAR(90)
) BEGIN
SELECT * FROM CraigslistSites WHERE country LIKE country_param;
END //