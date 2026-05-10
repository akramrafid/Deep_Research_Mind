# streamlit-debug

Debug Streamlit applications, fix rerun issues, optimize UI performance, and resolve component issues.

## When to Use

- Streamlit app crashes or fails to load
- st.rerun() or st.experimental_rerun() not working
- Session state issues (state not persisting)
- Slow UI rendering or component loading issues
- Widget callback not firing
- Deployment issues (missing dependencies, port conflicts)

## How to Debug

1. Check `app.py` for Streamlit API usage
2. Verify session state initialization patterns
3. Look for blocking operations in callbacks
4. Check component compatibility with Streamlit version
5. Review logs for specific error messages

## Tools to Use

- Grep: Search for `st\.`, `session_state`, `rerun`
- Read: Inspect app.py for component issues
- Bash: Run `streamlit run app.py --server.headless true` for debugging