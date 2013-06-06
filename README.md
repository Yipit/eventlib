# Eventlib

[![Build Status](https://secure.travis-ci.org/Yipit/eventlib.png)](http://travis-ci.org/Yipit/eventlib)

Long story short, eventlib is an asynchronous event tracking app for
Django. This library was built upon the following values:

 * It must be deadly simple to log an event;
 * It must be possible to track each event in different ways;
 * Each different "event handler" must be completely separate and fail
   gracefully;
 * The event system must be asynchronous, so let's use celery;
 * The library must be extensible;
 * 100% of test coverage is enough.

To learn how it works, please refer to our tutorial:

 1. [First steps to log an event](docs/p1-tutorial.md)
 2. [Declaring an event](docs/p2-declaring-an-event.md)
 3. [Asynchronous logging](docs/p3-asynchronous-logging.md)
