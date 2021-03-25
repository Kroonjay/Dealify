DELIMITER //
CREATE PROCEDURE CreateDealifySearch (
  IN search_name_param NVARCHAR(90),
  IN sources_param JSON,
  IN search_config_param JSON
) BEGIN
INSERT INTO
  DealifySearches (
    search_name,
    sources,
    search_config
  )
VALUES
  (
    search_name_param,
    sources_param,
    search_config_param
  );
END //