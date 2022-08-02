create_table_if_not_exist = '''
    CREATE TABLE IF NOT EXISTS peers(
        peer_id bigint PRIMARY KEY,
        peer_group varchar(30) NOT NULL,
        url varchar(100) NOT NULL,
        method varchar(20),
        hours smallint,
        amount smallint,
        subscribed boolean NOT NULL)
'''

select_peer_group = '''
    SELECT peer_group
    FROM peers
    WHERE peer_id = $1
'''

select_peer_url = '''
    SELECT url
    FROM peers
    WHERE peer_id = $1
'''

select_peer_method = '''
    SELECT method
    FROM peers
    WHERE peer_id = $1
'''

select_peer_hours = '''
    SELECT hours
    FROM peers
    WHERE peer_id = $1
'''

select_peer_amount = '''
    SELECT amount
    FROM peers
    WHERE peer_id = $1
'''

is_peer_subscribed = '''
    SELECT subscribed
    FROM peers
    WHERE peer_id = $1
'''

is_peer_in_db = '''
    SELECT exists (SELECT 1 FROM peers WHERE peer_id = $1 LIMIT 1)
'''

add_new_peer = '''
    INSERT INTO peers (peer_id, peer_group, url, subscribed)
    VALUES ($1, $2, $3, false)
'''

update_existed_peer = '''
    UPDATE peers
    SET peer_group = $1, url = $2
    WHERE peer_id = $3
'''

set_peer_method = '''
    UPDATE peers
    SET method = $1
    WHERE peer_id = $2
'''

set_peer_hours = '''
    UPDATE peers
    SET hours = $1
    WHERE peer_id = $2
'''

set_peer_amount = '''
    UPDATE peers
    SET amount = $1
    WHERE peer_id = $2
'''

set_peer_subscribe_state = '''
    UPDATE peers
    SET subscribed = $1
    WHERE peer_id = $2
'''

select_subscribed_peers = '''
    SELECT peer_id FROM peers WHERE subscribed = true
'''
