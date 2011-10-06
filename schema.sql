drop table if exists events;
drop table if exists news;


create table events(id, calendar_title TEXT, event_title TEXT, start_time INTEGER, end_time INTEGER,
                    location TEXT, status TEXT, description TEXT);
                    
                    
create table news(id INTEGER, post_title TEXT, post_date INTEGER, post_content TEXT, 
									post_category TEXT);