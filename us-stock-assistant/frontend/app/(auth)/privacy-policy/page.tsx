"use client";

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Privacy Policy</h1>
        <p className="text-sm text-gray-600 mb-8">Last Updated: {new Date().toLocaleDateString()}</p>

        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Introduction</h2>
            <p>Welcome to US Stock Assistant. We are committed to protecting your personal information and your right to privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our portfolio management application.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Information We Collect</h2>
            <p className="mb-2">We collect the following types of information:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Account Information:</strong> Email address, password (encrypted), and account preferences
              </li>
              <li>
                <strong>Portfolio Data:</strong> Stock positions, purchase prices, quantities, and transaction history
              </li>
              <li>
                <strong>Usage Data:</strong> How you interact with our application, including pages visited and features used
              </li>
              <li>
                <strong>Device Information:</strong> IP address, browser type, operating system, and device identifiers
              </li>
              <li>
                <strong>Preferences:</strong> Chart settings, notification preferences, and news source selections
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. How We Use Your Information</h2>
            <p className="mb-2">We use your information to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Provide and maintain our portfolio management services</li>
              <li>Display real-time stock prices and market data for your portfolio</li>
              <li>Generate AI-powered analysis and insights</li>
              <li>Send price alerts and notifications based on your preferences</li>
              <li>Improve our services and develop new features</li>
              <li>Ensure security and prevent fraud</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Data Sharing and Disclosure</h2>
            <p className="mb-2">We do not sell your personal information. We may share your information with:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Service Providers:</strong> Third-party companies that help us operate our application (e.g., cloud hosting, analytics)
              </li>
              <li>
                <strong>Financial Data Providers:</strong> To retrieve stock prices and market data via secure APIs
              </li>
              <li>
                <strong>Legal Requirements:</strong> When required by law or to protect our rights and safety
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Data Security</h2>
            <p>We implement industry-standard security measures to protect your information, including encryption of sensitive data, secure HTTPS connections, and regular security audits. However, no method of transmission over the internet is 100% secure, and we cannot guarantee absolute security.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Your Rights (GDPR & CCPA)</h2>
            <p className="mb-2">You have the following rights regarding your personal data:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Access:</strong> Request a copy of all personal data we hold about you
              </li>
              <li>
                <strong>Correction:</strong> Request correction of inaccurate or incomplete data
              </li>
              <li>
                <strong>Deletion:</strong> Request deletion of your personal data (right to be forgotten)
              </li>
              <li>
                <strong>Portability:</strong> Request your data in a machine-readable format
              </li>
              <li>
                <strong>Opt-Out:</strong> Opt out of marketing communications and certain data processing activities
              </li>
              <li>
                <strong>Non-Discrimination:</strong> We will not discriminate against you for exercising your privacy rights
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Data Retention</h2>
            <p>We retain your personal information for as long as your account is active or as needed to provide services. If you request account deletion, we will remove all personal data within 30 days, except where we are required to retain it for legal compliance.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Cookies and Tracking</h2>
            <p>We use cookies and similar tracking technologies to maintain your session, remember your preferences, and analyze usage patterns. You can control cookie settings through your browser preferences.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Children's Privacy</h2>
            <p>Our service is not intended for users under 18 years of age. We do not knowingly collect personal information from children.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Changes to This Policy</h2>
            <p>We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new policy on this page and updating the "Last Updated" date.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">11. Contact Us</h2>
            <p>If you have questions about this Privacy Policy or wish to exercise your privacy rights, please contact us at:</p>
            <p className="mt-2">
              Email: privacy@usstockassistant.com
              <br />
              Address: [Your Company Address]
            </p>
          </section>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <a href="/login" className="text-blue-600 hover:text-blue-800 font-medium">
            ← Back to Login
          </a>
        </div>
      </div>
    </div>
  );
}
