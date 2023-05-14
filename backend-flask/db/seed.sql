-- this file was manually created
INSERT INTO public.users (display_name, email, handle, cognito_user_id)
VALUES
  ('Philemon Nwanne', 'nwanne63@gmail.com', 'philemonnwanne', 'MOCK');
  ('Yondaime Hokage', 'yondaimehokage@mail.com', 'yondaimehokage', 'MOCK');
  ('Jermain Cole', 'jermainecole@mail.com', 'jermainecole', 'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'philemonnwanne' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )