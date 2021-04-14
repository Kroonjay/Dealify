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

read_craigslist_site_ids_by_state_sproc = "ReadCraigslistSiteIdsByState"

# Values: @search_id_param
read_dealify_search_by_id_sproc = "ReadDealifySearchById"

read_next_overdue_craigslist_query_id_sproc = "ReadNextOverdueCraigslistQueryId"
# Values: @query_id_param
start_overdue_craigslist_query_sproc = "StartOverdueCraigslistQuery"
# Values: @query_id_param
finish_craigslist_query_sproc = "FinishCraigslistQuery"
# Values: @search_id_param
user_disable_dealify_search_sproc = "UserDisableDealifySearch"
# Values: @search_id_param, @limit_param
read_craigslist_items_by_search_id_sproc = "ReadCraigslistItemsBySearchId"
# Values: @task_name_param, @task_type_param, @task_status_param, @task_config_param
create_dealify_search_task_sproc = "CreateDealifySearchTask"
# Values: @task_id_param
read_dealify_task_by_id_sproc = "ReadDealifySearchTaskById"

start_next_dealify_search_task_sproc = "StartNextDealifySearchTask"

set_overdue_craigslist_queries_sproc = "SetOverdueCraigslistQueries"

read_new_dealify_search_ids_sproc = "ReadNewDealifySearchIds"
# Values: @search_id_param
set_dormant_dealify_search_sproc = "SetDormantDealifySearch"
# Values: @worker_name_param, @task_config_param
create_dealify_worker_sproc = "CreateDealifyWorker"
# Values: @worker_id_param
read_dealify_worker_by_id_sproc = "ReadDealifyWorkerById"
# Values: @worker_id_param, @worker_status_param
update_dealify_worker_status_sproc = "UpdateDealifyWorkerStatus"

read_dealify_task_ids_by_type_sproc = "ReadDealifyTaskIdsByType"
# Values: @worker_id_param, @current_task_param
update_dealify_current_task_by_id_sproc = "UpdateDealifyCurrentTaskById"
# Values: @item_id_param
set_deleted_craigslist_item_sproc = "SetDeletedCraigslistItem"
# Values: @interval_days_param, @limit_param
read_old_craigslist_items_sproc = "ReadOldActiveCraigslistItems"

update_craigslist_item_status_sproc = "UpdateCraigslistItemStatus"

# Values: @status_param, @limit_param
read_craigslist_queries_by_status_sproc = "ReadCraigslistQueriesByStatus"
# Values: @query_id_param, @new_status_param
update_craigslist_query_status_sproc = "UpdateCraigslistQueryStatus"
# Values: @site_id_param
read_craigslist_site_by_id_sproc = "ReadCraigslistSiteById"
