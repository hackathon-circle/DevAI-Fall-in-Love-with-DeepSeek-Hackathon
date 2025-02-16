'use strict';

/* eslint-env browser */
/**
 * @module HTML
 */
/**
 * Module dependencies.
 */

var Base = require('./base');
var utils = require('../utils');
var escapeRe = require('escape-string-regexp');
var constants = require('../runner').constants;
var EVENT_TEST_PASS = constants.EVENT_TEST_PASS;
var EVENT_TEST_FAIL = constants.EVENT_TEST_FAIL;
var EVENT_SUITE_BEGIN = constants.EVENT_SUITE_BEGIN;
var EVENT_SUITE_END = constants.EVENT_SUITE_END;
var EVENT_TEST_PENDING = constants.EVENT_TEST_PENDING;
var escape = utils.escape;

/**
 * Save timer references to avoid Sinon interfering (see GH-237).
 */

var Date = global.Date;

/**
 * Expose `HTML`.
 */

exports = module.exports = HTML;

/**
 * Stats template: Result, progress, passes, failures, and duration.
 */

var statsTemplate =
  '<ul id="mocha-stats">' +
  '<li class="result"></li>' +
  '<li class="progress-contain"><progress class="progress-element" max="100" value="0"></progress><svg class="progress-ring"><circle class="ring-flatlight" stroke-dasharray="100%,0%"/><circle class="ring-highlight" stroke-dasharray="0%,100%"/></svg><div class="progress-text">0%</div></li>' +
  '<li class="passes"><a href="javascript:void(0);">passes:</a> <em>0</em></li>' +
  '<li class="failures"><a href="javascript:void(0);">failures:</a> <em>0</em></li>' +
  '<li class="duration">duration: <em>0</em>s</li>' +
  '</ul>';

var playIcon = '&#x2023;';

/**
 * Constructs a new `HTML` reporter instance.
 *
 * @public
 * @class
 * @memberof Mocha.reporters
 * @extends Mocha.reporters.Base
 * @param {Runner} runner - Instance triggers reporter actions.
 * @param {Object} [options] - runner options
 */
function HTML(runner, options) {
  Base.call(this, runner, options);

  var self = this;
  var stats = this.stats;
  var stat = fragment(statsTemplate);
  var items = stat.getElementsByTagName('li');
  const resultIndex = 0;
  const progressIndex = 1;
  const passesIndex = 2;
  const failuresIndex = 3;
  const durationIndex = 4;
  /** Stat item containing the root suite pass or fail indicator (hasFailures ? '✖' : '✓') */
  var resultIndicator = items[resultIndex];
  /** Passes text and count */
  const passesStat = items[passesIndex];
  /** Stat item containing the pass count (not the word, just the number) */
  const passesCount = passesStat.getElementsByTagName('em')[0];
  /** Stat item linking to filter to show only passing tests */
  const passesLink = passesStat.getElementsByTagName('a')[0];
  /** Failures text and count */
 
