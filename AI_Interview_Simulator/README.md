# TODO

- [x] Update frontend submit logic in `AI_Interview_Simulator/users/templates/interviewsession.html`:
  - [x] Normalize `question` to a string for backend compatibility.
  - [x] Iterate through `answersData` and POST one answer per request to `/api/interviews/submit-answer/`.
  - [x] Include `Authorization: Bearer <token>` for each request.
  - [x] Add cosole logs + user-visible errors for failures.
  - [x] Redirect to `/interview/report/` only after all submissions succeed.


