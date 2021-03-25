DELIMITER //
CREATE PROCEDURE ReadCraigslistSubdomainBySiteId (
    IN site_id_param INT
) BEGIN
SELECT subdomain FROM CraigslistSites WHERE site_id <=> site_id_param;
END //