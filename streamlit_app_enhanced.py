File "/mount/src/ai_new_update/streamlit_app_enhanced.py", line 682, in <module>
    main()
    ~~~~^^
File "/mount/src/ai_new_update/streamlit_app_enhanced.py", line 598, in main
    display_peptide_analysis(peptide, analysis_result)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/mount/src/ai_new_update/streamlit_app_enhanced.py", line 272, in display_peptide_analysis
    st.plotly_chart(fig, use_container_width=True)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 443, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/plotly_chart.py", line 556, in plotly_chart
    plotly_chart_proto.id = compute_and_register_element_id(
                            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        "plotly_chart",
        ^^^^^^^^^^^^^^^
    ...<8 lines>...
        use_container_width=use_container_width,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/lib/utils.py", line 254, in compute_and_register_element_id
    _register_element_id(ctx, element_type, element_id)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/lib/utils.py", line 148, in _register_element_id
    raise StreamlitDuplicateElementId(element_type)
