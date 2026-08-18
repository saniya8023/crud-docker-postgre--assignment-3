CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

-- Seed initial records if empty
INSERT INTO tasks (title, done)
SELECT 'Buy groceries', false
WHERE NOT EXISTS (SELECT 1 FROM tasks);

INSERT INTO tasks (title, done)
SELECT 'Review OOP concepts', true
WHERE NOT EXISTS (SELECT 1 FROM tasks);

INSERT INTO tasks (title, done)
SELECT 'Connect CRUD to Dockerized Postgres', false
WHERE NOT EXISTS (SELECT 1 FROM tasks);