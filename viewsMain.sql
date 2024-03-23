
---------------------------Notes----------------------------------
-- the 't' in t(jkey) stood for telem but kept throughout for consistancy. if curious. 
---- $$ == string constants. allows execute blocks of commands without having to define a full function

-- NEED TO DO TEXT_LOG STILL. execute was null?

-- skipped INFO indidriver_start due to non having values

---------------------End Notes------------------------------------
--
------------------------telem_cooler--------------------------------
DO $$
DECLARE keys text;
BEGIN
    DROP VIEW IF EXISTS telem_cooler cascade;
    SELECT string_agg(distinct format('msg->> %L as %I', jkey, jkey), ', ') -- single quotes 4 str
     INTO keys
     FROM telemetry, jsonb_object_keys("msg") as t(jkey)
     WHERE ec = 'telem_cooler';
     EXECUTE 'CREATE VIEW telem_cooler AS SELECT device, ts, prio, ec,' ||keys||' FROM telemetry
    WHERE prio = ''TELM'' ';
END;
$$;

---------------------------telem_fxngen------------------------------------
-- DO $$
-- DECLARE keys text;
-- BEGIN
--      DROP VIEW IF EXISTS telem_fxngen cascade;
--      SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
--      INTO keys
--      FROM telemetry, jsonb_object_keys("msg") as t(jkey)
--      WHERE ec = 'telem_fxngen';

--      EXECUTE 'CREATE VIEW telem_fxngen AS SELECT device, ts, prio, ec,' ||keys||' FROM telemetry
--      WHERE ec = ''telem_fxngen'' ';

-- END;
-- $$;

--------------------------telem_observer-------------------------------------
DO $$
DECLARE keys text;
BEGIN    
     DROP VIEW IF EXISTS telem_observer cascade;
     SELECT string_agg(DISTINCT format('msg ->> %L as %I', jkey, jkey), ', ')
     INTO keys
     FROM telemetry, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'telem_observer';

     EXECUTE 'CREATE VIEW telem_observer AS SELECT device, ts, prio, ec,' ||keys|| ' FROM telemetry
     WHERE ec = ''telem_observer''';
END;
$$;

---------------------------info_config_log----------------------------
DO $$ 
DECLARE keys text;
BEGIN
     DROP VIEW IF EXISTS info_config_log;
     SELECT string_agg(DISTINCT format('msg ->> %L as %I', jkey, jkey), ', ')
     INTO keys
     FROM info, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'config_log';

     EXECUTE 'CREATE VIEW info_config_log AS 
     SELECT device, ts, prio, ec, ' ||keys|| ' FROM info 
     WHERE ec = ''config_log'' ';
END;
$$;

---------------------------info_state_change------------------------
DO $$
DECLARE keys text;
BEGIN 
     DROP VIEW IF EXISTS info_state_change CASCADE;
     SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
     INTO keys
     FROM info, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'state_change';

     EXECUTE 'CREATE VIEW info_state_change 
          AS SELECT device, ts, prio, ec, ' ||keys|| ' 
          FROM info
          WHERE ec = ''state_change'' ';

END;
$$;
------------------------err_software_log----------------------------
DO $$
DECLARE keys text;
BEGIN 
     DROP VIEW IF EXISTS err_software_log CASCADE;
     SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
     INTO keys
     FROM info, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'software_log';
     --
     EXECUTE 'CREATE VIEW err_software_log
               AS SELECT device, ts, prio, ec, ' ||keys|| '
               FROM info
               WHERE ec = ''software_log'' ';
END;
$$;

------------------------info_outlet_state----------------------------
DO $$
DECLARE keys text;
BEGIN 
     DROP VIEW IF EXISTS info_outlet_state CASCADE;
     SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
     INTO keys
     FROM info, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'outlet_state';
     EXECUTE 'CREATE VIEW info_outlet_state
               AS SELECT device, ts, prio, ec, ' || keys || '
               FROM info
               WHERE ec = ''outlet_state'' ';
END;
$$;

------------------------info_outlet_channel_state--------------------
DO $$
DECLARE keys text;
BEGIN
     DROP VIEW IF EXISTS info_outlet_channel_state CASCADE;
     SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
     INTO keys
     FROM info, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'outlet_channel_state';

     EXECUTE 'CREATE VIEW info_outlet_channel_state
               AS SELECT device, ts, prio, ec, ' ||keys|| '
               FROM info 
               WHERE ec = ''outlet_channel_state'' ';
END;
$$;

------------------------info_observer----------------------------
DO $$
DECLARE keys text;
BEGIN
     DROP VIEW IF EXISTS info_observer CASCADE;
     SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
     INTO keys
     FROM info, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'observer';

     EXECUTE 'CREATE VIEW info_observer
               AS SELECT device, ts, prio, ec, ' ||keys|| '
               FROM info
               WHERE ec = ''observer'' ';
END;
$$;

------------------------info_text_log----------------------------
DO $$
DECLARE keys text;
BEGIN
     DROP VIEW IF EXISTS info_text_log CASCADE;
     SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
     INTO keys
     FROM info, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'text_log';
     EXECUTE 'CREATE VIEW info_text_log
          AS SELECT device, ts, prio, ec,' ||keys|| '
          FROM info
          WHERE ec = ''text_log'' ';
END;
$$;

------------------------file_modified----------------------------
DO $$
DECLARE keys text;
BEGIN
     DROP VIEW IF EXISTS file_modified CASCADE;
     SELECT string_agg(DISTINCT format('msg ->> %L AS %I', jkey, jkey), ', ')
     INTO keys
     FROM file_system, jsonb_object_keys("msg") AS t(jkey)
     WHERE ec = 'file_modified';

     EXECUTE 'CREATE VIEW file_modified
               AS SELECT device, ts, ec, ' ||keys|| '
               FROM file_system
               WHERE ec = ''file_modified'' ';
END;
$$;