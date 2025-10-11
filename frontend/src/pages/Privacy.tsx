import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";

export function Privacy() {
  const { t } = useTranslation();

  return (
    <>
      <Helmet>
        <title>{t("legal.privacy")} - NMTSA Learn</title>
        <meta
          content="Privacy Policy for NMTSA Learn platform"
          name="description"
        />
      </Helmet>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>

        <div className="prose prose-lg max-w-none">
          <p className="text-gray-600 mb-6">
            <strong>Last Updated:</strong> October 11, 2025
          </p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">1. Introduction</h2>
            <p className="text-gray-700 mb-4">
              NMTSA Learn (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;)
              is committed to protecting your privacy. This Privacy Policy
              explains how we collect, use, disclose, and safeguard your
              information when you visit our platform.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              2. Information We Collect
            </h2>

            <h3 className="text-xl font-semibold mb-3 mt-4">
              Personal Information
            </h3>
            <p className="text-gray-700 mb-4">
              We collect information that you provide directly to us, including:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>
                Name and contact information (email address, phone number)
              </li>
              <li>Account credentials (username and password)</li>
              <li>Profile information (bio, photo, preferences)</li>
              <li>Course enrollment and progress data</li>
              <li>
                Payment information (processed securely through third-party
                payment processors)
              </li>
              <li>Communications you send to us</li>
            </ul>

            <h3 className="text-xl font-semibold mb-3 mt-4">
              Automatically Collected Information
            </h3>
            <p className="text-gray-700 mb-4">
              When you access our Platform, we automatically collect certain
              information, including:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>IP address and browser type</li>
              <li>Device information and operating system</li>
              <li>Usage data (pages visited, time spent, click patterns)</li>
              <li>Cookies and similar tracking technologies</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              3. How We Use Your Information
            </h2>
            <p className="text-gray-700 mb-4">
              We use the information we collect to:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Provide, maintain, and improve our Platform</li>
              <li>Process course enrollments and track your progress</li>
              <li>
                Send you course updates, certificates, and administrative
                information
              </li>
              <li>Respond to your comments, questions, and requests</li>
              <li>Personalize your learning experience</li>
              <li>Analyze usage patterns and trends</li>
              <li>
                Detect, prevent, and address technical issues and security
                threats
              </li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              4. Sharing Your Information
            </h2>
            <p className="text-gray-700 mb-4">
              We may share your information with:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>
                <strong>Course Instructors:</strong> We share your progress and
                performance data with instructors of courses you&apos;re
                enrolled in
              </li>
              <li>
                <strong>Service Providers:</strong> Third-party vendors who
                perform services on our behalf (hosting, analytics, payment
                processing)
              </li>
              <li>
                <strong>Legal Requirements:</strong> When required by law or to
                protect our rights and safety
              </li>
              <li>
                <strong>Business Transfers:</strong> In connection with any
                merger, sale, or acquisition of all or part of our business
              </li>
            </ul>
            <p className="text-gray-700 mb-4">
              We do not sell your personal information to third parties.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">5. Data Security</h2>
            <p className="text-gray-700 mb-4">
              We implement appropriate technical and organizational security
              measures to protect your personal information against unauthorized
              access, alteration, disclosure, or destruction. These measures
              include:
            </p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Encryption of data in transit and at rest</li>
              <li>Regular security assessments and updates</li>
              <li>Access controls and authentication mechanisms</li>
              <li>Employee training on data protection</li>
            </ul>
            <p className="text-gray-700 mb-4">
              However, no method of transmission over the Internet or electronic
              storage is 100% secure, and we cannot guarantee absolute security.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              6. Your Rights and Choices
            </h2>
            <p className="text-gray-700 mb-4">You have the right to:</p>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>
                <strong>Access:</strong> Request a copy of the personal
                information we hold about you
              </li>
              <li>
                <strong>Correction:</strong> Request correction of inaccurate or
                incomplete information
              </li>
              <li>
                <strong>Deletion:</strong> Request deletion of your personal
                information
              </li>
              <li>
                <strong>Opt-out:</strong> Unsubscribe from marketing
                communications
              </li>
              <li>
                <strong>Data Portability:</strong> Request a copy of your data
                in a portable format
              </li>
              <li>
                <strong>Object:</strong> Object to processing of your personal
                information
              </li>
            </ul>
            <p className="text-gray-700 mb-4">
              To exercise these rights, please contact us at
              privacy@nmtsalearn.org
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              7. Cookies and Tracking Technologies
            </h2>
            <p className="text-gray-700 mb-4">
              We use cookies and similar tracking technologies to track activity
              on our Platform and hold certain information. You can instruct
              your browser to refuse all cookies or to indicate when a cookie is
              being sent.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              8. Children&apos;s Privacy
            </h2>
            <p className="text-gray-700 mb-4">
              Our Platform is not intended for children under 13 years of age.
              We do not knowingly collect personal information from children
              under 13. If you are a parent or guardian and believe your child
              has provided us with personal information, please contact us.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              9. International Data Transfers
            </h2>
            <p className="text-gray-700 mb-4">
              Your information may be transferred to and maintained on servers
              located outside of your state, province, country, or other
              governmental jurisdiction where data protection laws may differ.
              By using our Platform, you consent to such transfers.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">
              10. Changes to This Privacy Policy
            </h2>
            <p className="text-gray-700 mb-4">
              We may update our Privacy Policy from time to time. We will notify
              you of any changes by posting the new Privacy Policy on this page
              and updating the &quot;Last Updated&quot; date.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">11. Contact Us</h2>
            <p className="text-gray-700 mb-4">
              If you have any questions about this Privacy Policy, please
              contact us at:
            </p>
            <p className="text-gray-700">
              Email: privacy@nmtsalearn.org
              <br />
              Address: New Mexico Tribal Safety Alliance
              <br />
              Phone: (555) 123-4567
            </p>
          </section>
        </div>
      </div>
    </>
  );
}
