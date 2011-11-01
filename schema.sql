drop table if exists events;
drop table if exists news;


create table events(id, updated TEXT, calendar_title TEXT, event_title TEXT, start_time INTEGER, 
                    end_time INTEGER, location TEXT, status TEXT, description TEXT, 
                    is_all_day INTEGER, thumbnail TEXT, full_image TEXT);
                    
                    
create table news(id INTEGER, post_title TEXT, post_date INTEGER, post_content TEXT, 
				  post_category TEXT);