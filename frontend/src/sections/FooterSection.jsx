const FooterSection = () => {
  return (
    <section className="bg-white py-8">
      <div className="max-w-7xl mx-auto px-5 md:px-10">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-gray-600 text-sm">
          <p>Made by team GitGoneWild - Redact 2025</p>
          <div className="flex items-center gap-7">
            <p className="cursor-pointer hover:text-gray-900">Privacy Policy</p>
            <p className="cursor-pointer hover:text-gray-900">Terms of Service</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FooterSection;
