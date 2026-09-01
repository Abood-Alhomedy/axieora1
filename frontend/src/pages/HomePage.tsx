import { useEffect } from 'react'
import { useGlobalFunctions } from '../functions/GlobalFunctions'
import ScrollRobot from './ScrollRobot'
import Spline from '@splinetool/react-spline'



export default function HomePage() {

  const {

    agents,

    workflows,

    loadAgents,

    loadWorkflows

  } = useGlobalFunctions()


  useEffect(() => {

    loadAgents()

    loadWorkflows()

  }, [

    loadAgents,

    loadWorkflows

  ])


  return (


    <>
      {/* <Spline
        scene="https://prod.spline.design/SQMevr1H0rHx5n-s/scene.splinecode"
        onLoad={() => console.log('تم تحميل المشهد بنجاح!')}
        onError={(error) => console.error('خطأ في التحميل:', error)}
      /> */}
      <ScrollRobot />

      <div className="page-header">

        <h1 className="page-title">

          Microsoft Agent Framework Code Builder

        </h1>

      </div>


      <p
        style={{

          color:
            'var(--text-secondary)',

          marginBottom: 32,

          maxWidth: 680,

          lineHeight: 1.7,

          fontSize: 14

        }}
      >

        إنشاء كود وكلاء الذكاء الاصطناعي وسير العمل تلقائيًا باستخدام اللغة الطبيعية.
        باستخدام مهارات Microsoft Agent Framework، يمكنك إنشاء الكود وتحريره واختباره بشكل تفاعلي.

      </p>


      <div className="grid-home">


        <div className="card">

          <div className="card-title">

            🤖 الوكلاء

          </div>


          <p className="stat-value">

            {agents.length}

          </p>


          <p className="stat-label">

            الوكلاء المُنشأون

          </p>

        </div>


        <div className="card">

          <div className="card-title">

            🔀 سير العمل

          </div>


          <p className="stat-value">

            {workflows.length}

          </p>


          <p className="stat-label">

            مسارات العمل المُنشأة

          </p>

        </div>


      </div>


      <div
        className="card"
        style={{

          marginTop: 24,

          maxWidth: 680

        }}
      >

        <div
          className="card-title"
          style={{

            marginBottom: 12

          }}
        >

          البنية المعمارية

        </div>


        <pre className="code-block">

          {`
┌─────────────────────────────────────────┐
│       الواجهة الأمامية (React + TS)     │
│                                         │
│              GlobalFunctions            │
│                     │                   │
│         ┌───────────┼───────────┐       │
│         ▼           ▼           ▼       │
│      الوكلاء    سير العمل    البيانات    │
└─────────────────────────────────────────┘
                 │
                 ▼
              REST API
                 │
                 ▼
┌─────────────────────────────────────────┐
│         الواجهة الخلفية FastAPI         │
└─────────────────────────────────────────┘
`.trim()}

        </pre>

      </div>


    </>

  )

}