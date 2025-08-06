TABLE mood, card, project
FROM "Draw One/Daily"
WHERE mood
SORT file.name DESC
LIMIT 7
