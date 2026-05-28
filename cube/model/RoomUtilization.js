cube(`RoomUtilization`, {
  sql: `SELECT * FROM gallery.gallery_occupancy_5m`,

  measures: {
    activeVisitors: {
      sql: `active_visitors`,
      type: `max`,
      title: `ActiveVisitors`
    },

    roomUtilization: {
      sql: `active_visitors / 150.0`,
      type: `avg`,
      format: `percent`,
      title: `RoomUtilization`
    },

    views: {
      sql: `views`,
      type: `sum`,
      title: `RealtimeViews`
    },

    likes: {
      sql: `likes`,
      type: `sum`,
      title: `RealtimeLikes`
    }
  },

  dimensions: {
    windowStart: {
      sql: `window_start`,
      type: `time`
    },

    exhibitionId: {
      sql: `exhibition_id`,
      type: `string`
    },

    roomId: {
      sql: `room_id`,
      type: `string`
    }
  }
});
