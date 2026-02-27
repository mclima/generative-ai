"use client";

export default function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Terms of Service</h1>
        <p className="text-sm text-gray-600 mb-8">Last Updated: {new Date().toLocaleDateString()}</p>

        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h2>
            <p>By accessing and using US Stock Assistant ("the Service"), you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Description of Service</h2>
            <p>US Stock Assistant is a portfolio management application that provides stock tracking, real-time market data, AI-powered analysis, and automated alerts. The Service is provided for informational purposes only and does not constitute financial advice.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. User Accounts</h2>
            <p className="mb-2">When creating an account, you agree to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Provide accurate and complete information</li>
              <li>Maintain the security of your password and account</li>
              <li>Notify us immediately of any unauthorized access</li>
              <li>Be responsible for all activities under your account</li>
              <li>Not share your account credentials with others</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Acceptable Use</h2>
            <p className="mb-2">You agree NOT to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Use the Service for any illegal purpose</li>
              <li>Attempt to gain unauthorized access to our systems</li>
              <li>Interfere with or disrupt the Service</li>
              <li>Use automated systems to access the Service without permission</li>
              <li>Reverse engineer or attempt to extract source code</li>
              <li>Resell or redistribute the Service without authorization</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Investment Disclaimer</h2>
            <p className="font-semibold mb-2">IMPORTANT: This Service is NOT financial advice.</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>All information provided is for informational purposes only</li>
              <li>We are not registered investment advisors or broker-dealers</li>
              <li>Past performance does not guarantee future results</li>
              <li>You are solely responsible for your investment decisions</li>
              <li>Consult with a qualified financial advisor before making investment decisions</li>
              <li>Stock market investments carry risk, including potential loss of principal</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Data Accuracy</h2>
            <p>While we strive to provide accurate and up-to-date information, we do not guarantee the accuracy, completeness, or timeliness of stock prices, market data, or AI-generated analysis. Data may be delayed or contain errors. Always verify information from official sources before making investment decisions.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Intellectual Property</h2>
            <p>All content, features, and functionality of the Service, including but not limited to text, graphics, logos, and software, are owned by US Stock Assistant and protected by copyright, trademark, and other intellectual property laws.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Limitation of Liability</h2>
            <p className="mb-2">TO THE MAXIMUM EXTENT PERMITTED BY LAW, US STOCK ASSISTANT SHALL NOT BE LIABLE FOR:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Any investment losses or financial damages</li>
              <li>Indirect, incidental, or consequential damages</li>
              <li>Loss of profits, data, or business opportunities</li>
              <li>Errors or inaccuracies in data or analysis</li>
              <li>Service interruptions or unavailability</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Indemnification</h2>
            <p>You agree to indemnify and hold harmless US Stock Assistant from any claims, damages, losses, or expenses arising from your use of the Service, violation of these Terms, or infringement of any third-party rights.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Service Modifications</h2>
            <p>We reserve the right to modify, suspend, or discontinue the Service at any time without notice. We may also update these Terms from time to time. Continued use of the Service after changes constitutes acceptance of the new Terms.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">11. Account Termination</h2>
            <p>We reserve the right to terminate or suspend your account at any time for violation of these Terms or for any other reason. You may also terminate your account at any time through the Settings page.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">12. Privacy</h2>
            <p>Your use of the Service is also governed by our Privacy Policy. Please review our Privacy Policy to understand how we collect, use, and protect your information.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">13. Governing Law</h2>
            <p>These Terms shall be governed by and construed in accordance with the laws of [Your Jurisdiction], without regard to its conflict of law provisions.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">14. Dispute Resolution</h2>
            <p>Any disputes arising from these Terms or your use of the Service shall be resolved through binding arbitration in accordance with the rules of [Arbitration Organization].</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">15. Contact Information</h2>
            <p>If you have questions about these Terms of Service, please contact us at:</p>
            <p className="mt-2">
              Email: legal@usstockassistant.com
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
