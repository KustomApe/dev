// src/app/page.tsx の例
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-24">
      <div className="bg-white p-8 rounded-xl shadow-lg text-center">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">
          Next.js + Tailwind CSS!
        </h1>
        <p className="text-gray-600">
          このサイトは Vercel にデプロイされます。
        </p>
        <button className="mt-6 px-6 py-2 bg-black text-white rounded-full hover:bg-gray-800 transition">
          詳しく見る
        </button>
      </div>
    </main>
  );
}
