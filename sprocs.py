# Values: @search_name_param, @interval_mins_param, @search_config_param
create_dealify_search_sproc = "CreateDealifySearch"
# Values: @search_id_param, @query_param, @cl_site_param, @area_param, @category_param, @search_titles_param, @require_image_param, @posted_today_param
create_craigslist_query_sproc = "CreateCraigslistQuery"
# Values: @item_name_param, @price_param, @search_id_param, @source_url_param, @source_id_param, @posted_at_param, @is_deleted_param, @has_image_param, @last_updated_param, @repost_of_param, @item_location_param
create_craigslist_item_sproc = "CreateCraigslistItem"
create_craigslist_site_sproc = "CreateCraigslistSite"
read_craigslist_subdomain_by_site_id_sproc = "ReadCraigslistSubdomainBySiteId"
# Values: @country_param
read_craigslist_site_ids_by_country_sproc = "ReadCraigslistSiteIdsByCountry"
# Values: @search_id_param
read_dealify_search_by_id_sproc = "ReadDealifySearchById"

read_next_overdue_craigslist_query_id_sproc = "ReadNextOverdueCraigslistQueryId"
# Values: @query_id_param
start_overdue_craigslist_query_sproc = "StartOverdueCraigslistQuery"
# Values: @query_id_param
finish_craigslist_query_sproc = "FinishCraigslistQuery"
# Values: @search_id_param
user_disable_dealify_search_sproc = "UserDisableDealifySearch"
# Values: @search_id_param
read_craigslist_items_by_search_id_sproc = "ReadCraigslistItemsBySearchId"
# Values: @task_name_param, @task_type_param, @task_status_param, @task_config_param
create_dealify_search_task_sproc = "CreateDealifySearchTask"
# Values: @task_id_param
read_dealify_search_task_by_id_sproc = "ReadDealifySearchTaskById"

start_next_dealify_search_task_sproc = "StartNextDealifySearchTask"

set_overdue_craigslist_queries_sproc = "SetOverdueCraigslistQueries"
