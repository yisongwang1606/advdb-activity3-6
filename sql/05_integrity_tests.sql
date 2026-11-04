-- AI-assisted integrity checks. Rejected rows are rolled back in subtransactions.
DO $test$
BEGIN
    BEGIN
        INSERT INTO users VALUES (9001,'Invalid','invalid@example.com','CA','Basic','{}');
        RAISE EXCEPTION 'Missing genre array was accepted';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        INSERT INTO activity_logs VALUES (9001,99999,1,now(),'{"event_type":"play","minutes_watched":1}');
        RAISE EXCEPTION 'Orphan activity was accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL; END;
    BEGIN
        INSERT INTO activity_logs VALUES (9002,1,1,now(),'{"event_type":"rate","stars":6}');
        RAISE EXCEPTION 'Invalid rating was accepted';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        INSERT INTO activity_logs VALUES (9003,1,NULL,now(),'{"event_type":"play","minutes_watched":1}');
        RAISE EXCEPTION 'Play without title was accepted';
    EXCEPTION WHEN check_violation THEN NULL; END;
END
$test$;
