project(TestCTestRun)
cmake_minimum_required(VERSION 2.8)

enable_testing()
# include CTestConfig.cmake if present
INCLUDE(CTest)

FILE(GLOB pythonTests ./run*.py)
LIST(SORT pythonTests)

FOREACH(aTest ${pythonTests})

  execute_process(
    COMMAND ${aTest} --print-test-name
    OUTPUT_VARIABLE testName
    RESULT_VARIABLE testResult
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  execute_process(
    COMMAND ${aTest} --timeout
    OUTPUT_VARIABLE testTimeout
    RESULT_VARIABLE testResult2
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  IF(testResult OR testResult2)
    MESSAGE("Running ${aTest} failed ... not added")
  ELSE()
    MESSAGE("Adding ${aTest} as ${testName} with timeout ${testTimeout}")
    add_test(${testName} ${aTest})
    set_tests_properties (${testName} PROPERTIES TIMEOUT ${testTimeout})
  ENDIF()
ENDFOREACH(aTest)

