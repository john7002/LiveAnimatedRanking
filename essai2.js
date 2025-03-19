(function (global) {
  'use strict';

  var ITEM_HEIGHT = 13;

  var isUpdateStyleConstSaving = false;
  requestAnimationFrame(function updateStyleConst() {
    if (!isUpdateStyleConstSaving) {
      if (matchMedia('screen and (max-width: 600px)').matches) {
        ITEM_HEIGHT = 9;
      } else {
        ITEM_HEIGHT = 16;
      }
      isUpdateStyleConstSaving = true;
      setTimeout(function () { isUpdateStyleConstSaving = false; }, 1000 / 10);
    }
    requestAnimationFrame(updateStyleConst);
  });

  // {{{ Ranking
  /**
   * @class
   */
  function Ranking(node) {
    this.node = node;
    this.items = [];
    this.seUp = new Audio('http://jsrun.it/assets/9/X/R/9/9XR9q.ogg');
    this.seDown = new Audio('http://jsrun.it/assets/2/L/1/L/2L1LS.ogg');
    this.seUp.autoplay = false;
    this.seUp.loop = false;
    this.seUp.volume = 0.6;
    this.seDown.autoplay = false;
    this.seDown.loop = false;
    this.seDown.volume = 0.6;
  }

  /**
   * @param {RankingItem} item
   * @param {number}      order
   * @return {Ranking}
   */
  Ranking.prototype.insert = function (item, order) {
    var i = 0, iz = 0,
      me = this;

    order -= 0;
    item.order = order;
    this.items.splice(order - 1, 0, item);
    this.correctPosition();
    item.node.style.height = 0;
    item.node.style.opacity = 0;
    item.node.style.top = ((ITEM_HEIGHT + 2) * (order - 1)) + 'mm';
    this.node.appendChild(item.node);
    setTimeout(function () {
      me.node.style.height = ((ITEM_HEIGHT + 2) * me.items.length) + 2 + 'mm';
      item.node.style.height = ITEM_HEIGHT + 'mm';
      item.node.style.opacity = 1;
    }, 0);
    return this;
  };

  /**
   * @param {RankingItem} item
   * @return {Ranking}
   */
  Ranking.prototype.remove = function (item) {
    var i = 0, iz = 0,
      order = item.order;

    this.items.splice(order - 1, 1);
    item.node.style.height = 0;
    item.node.style.opacity = 0;
    setTimeout(function () {
      if (item.node.parentNode) {
        item.node.parentNode.removeChild(item.node);
      }
    }, 300);
    this.correctPosition();
    return this;
  };

  /**
   * @param {RankingItem} item
   * @param {number}      order
   * @return {Ranking}
   */
  Ranking.prototype.move = function (item, order) {
    var slideItem, startY = 0, endY = 0, i = 0, iz = 0, isDown = false,
      me = this;

    order -= 0;
    if (item.order === order) { return this; }
    if (item.order < order) { // move down
      startY = (ITEM_HEIGHT + 2) * (item.order - 1) + 4;
      endY = (ITEM_HEIGHT + 2) * (order - 1) - 4;
      this.seDown.pause();
      this.seDown.currentTime = 0;
      this.seDown.play();
      isDown = true;
    } else {                  // move up
      startY = (ITEM_HEIGHT + 2) * (item.order - 1) - 4;
      endY = (ITEM_HEIGHT + 2) * (order - 1) + 4;
      this.seUp.pause();
      this.seUp.currentTime = 0;
      this.seUp.play();
      isDown = false;
    }
    this.items.splice(item.order - 1, 1);
    this.items.splice(order - 1, 0, item);
    item.order = order;
    item.node.classList.add('ranking-item_moving');
    if (isDown) {
      item.node.classList.add('ranking-item_movingDown');
    } else {
      item.node.classList.add('ranking-item_movingUp');
    }
    item.node.style.top = startY + 'mm';
    item.node.style.zIndex = 1000;
    item.node.addEventListener('transitionend', function mainMove() {
      item.node.removeEventListener('transitionend', mainMove);
      item.node.style.top = endY + 'mm';
      setTimeout(function () {
        item.node.addEventListener('transitionend', function endMove() {
          item.node.removeEventListener('transitionend', endMove);
          item.node.classList.remove('ranking-item_moving');
          item.node.classList.remove('ranking-item_movingDown');
          item.node.classList.remove('ranking-item_movingUp');
          me.correctPosition();
          setTimeout(function () {
            item.node.addEventListener('transitionend', function finalizeMove() {
              item.node.removeEventListener('transitionend', finalizeMove);
              item.node.style.zIndex = 'auto';
            });
          }, 0);
        });
      }, 0);
    });
    this.correctPosition();
    return this;
  };

  Ranking.prototype.correctPosition = function () {
    var item, i = 0, iz = 0,
      itemsNum = this.items.length;

    for (i = 0, iz = itemsNum; i < iz; ++i) {
      item = this.items[i];
      item.order = i + 1;
      if (item.node.classList.contains('ranking-item_moving')) { continue; }
      item.node.style.height = ITEM_HEIGHT + 'mm';
      item.node.style.top = ((ITEM_HEIGHT + 2) * i) + 'mm';
    }
    this.node.style.height = ((ITEM_HEIGHT + 2) * itemsNum) + 2 + 'mm';
  };
  // }}} Ranking

  // {{{ RankingItem
  /**
   * @class
   */
  function RankingItem() {
    this.node = document.importNode(
      document.getElementById('ranking-item').content,
      true
    ).firstElementChild;
    this._order = 0;
    this._userId = 0;
    this._userName = '';
    this._score = 0;
    this.moveState = 0; // 0:NotMoveing 1:MoveStarting 2:Moving 3:MoveEnding
  }

  Object.defineProperty(RankingItem.prototype, 'order', {
    /** @return {number} */
    get: function () { return this._order; },
    set: function (v) {
      v -= 0;
      this._order = v;
      this.node.querySelector('.ranking-item-order').textContent = v;
    }
  });

  Object.defineProperty(RankingItem.prototype, 'userId', {
    /** @return {number} */
    get: function () { return this._userId; },
    set: function (v) {
      this._userId = v;
      this.node.dataset.userId = v;
    }
  });

  Object.defineProperty(RankingItem.prototype, 'userName', {
    /** @return {string} */
    get: function () { return this._userName; },
    set: function (v) {
      this._userName = v;
      this.node.querySelector('.ranking-item-userName').textContent = v;
    }
  });

  Object.defineProperty(RankingItem.prototype, 'score', {
    /** @return {number} */
    get: function () { return this._score; },
    set: function (v) {
      var current = this._score,
        node = this.node.querySelector('.ranking-item-score');

      function change() {
        if (current < v) {
          current += Math.ceil((v - current) / 10);
        } else if (v < current) {
          current -= Math.ceil((current - v) / 10);
        }
        node.textContent = current + '';
        if (current !== v) { requestAnimationFrame(change); }
      }

      v -= 0;
      this._score = v;
      requestAnimationFrame(change);
    }
  });
  // }}} RankingItem

  // {{{ RankingApp
  /**
   * @class
   */
  function RankingApp(selector) {
    this.ranking = new Ranking(document.querySelector(selector));
  }

  /**
   * @return {RankingApp}
   */
  RankingApp.prototype.start = function () {
    var me = this;

    // this.fetchRanking().then(function (datas) {
    //   me.ranking.update(datas);
    // });
    // setInterval(function () {
    //   me.fetchRanking().then(function (datas) {
    //     me.ranking.update(datas);
    //   });
    // }, 1000);
    return this;
  };

  /**
   */
  RankingApp.prototype.fetchRanking = function () {
    var me = this,
      req = new XMLHttpRequest();

    req.open('GET', '/api/ranking');
    return new Promise(function (resolve, reject) {
      req.onreadystatechange = function () {
        if (req.readyState !== 4) { return; }
        if (req.status !== 200) { return reject(req); }
        resolve(JSON.parse(req.responseText));
      };
      req.send();
    });
  };
  // }}} RankingApp

  global['RankingItem'] = RankingItem;
  global['RankingApp'] = RankingApp;
}(this));
// vim:fdm=marker:
