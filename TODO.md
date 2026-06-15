# TODO - Pagination/filtering/sorting for GET /tasks

- [ ] Update schemas with a new paginated list response model (`TaskListOut`).
- [x] Implement pagination/filtering/sorting query params on `GET /tasks`.

- [ ] Add total-count query and return `{items,total,skip,limit}`.
- [ ] Add basic search (`q`) across `title` and `description`.
- [ ] Validate `sort_by` and `sort_dir` (return 400 for invalid values).
- [ ] Run the API and manually verify queries from the docs/swaggers.

