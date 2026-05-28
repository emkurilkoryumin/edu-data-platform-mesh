cube(`ArtworkEngagement`, {
  sql: `SELECT * FROM gallery.gold_artwork_engagement_daily`,

  measures: {
    studentCount: {
      sql: `student_count`,
      type: `sum`,
      title: `StudentCount`
    },

    artworkCount: {
      sql: `artwork_count`,
      type: `sum`,
      title: `ArtworkCount`
    },

    views: {
      sql: `views`,
      type: `sum`,
      title: `Views`
    },

    likes: {
      sql: `likes`,
      type: `sum`,
      title: `Likes`
    },

    avgGrade: {
      sql: `avg_moderation_score`,
      type: `avg`,
      title: `AvgGrade`
    }
  },

  dimensions: {
    eventDate: {
      sql: `event_date`,
      type: `time`
    },

    exhibitionId: {
      sql: `exhibition_id`,
      type: `string`
    },

    category: {
      sql: `category`,
      type: `string`
    },

    ageGroup: {
      sql: `age_group`,
      type: `string`
    }
  }
});
