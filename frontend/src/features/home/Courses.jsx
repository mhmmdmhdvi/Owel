import { coursesIntro, courses } from './coursesContent.js';

function CourseCard({ course }) {
  return (
    <article className="course-card">
      <div className="course-meta"><span>{course.topic}</span></div>
      <h3>{course.title}</h3>
      <p className="course-sessions">{course.sessions}</p>
      <details className="course-subjects">
        <summary>سرفصل‌ها</summary>
        <p>{course.description}</p>
        <ul>{course.subjects.map((subject) => <li key={subject}>{subject}</li>)}</ul>
      </details>
      <div className="course-price"><span>{course.category === 'free' ? 'دسترسی نامحدود' : 'هزینه دوره'}</span><strong>{course.price}</strong></div>
    </article>
  );
}

export default function Courses() {
  return (
    <section id="classes" className="courses-section content-section" aria-labelledby="courses-title">
      <div className="page-shell">
        <div className="content-heading"><span className="eyebrow">{coursesIntro.eyebrow}</span><h2 id="courses-title">{coursesIntro.title}</h2><p>{coursesIntro.description}</p></div>
        <div className="course-grid">
          {courses.map((course) => <CourseCard key={course.id} course={course} />)}
        </div>
      </div>
    </section>
  );
}
