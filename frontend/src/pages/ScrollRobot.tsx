"use client";

import Spline from "@splinetool/react-spline";
import { useEffect, useRef } from "react";

export default function ScrollRobot() {
  const robotRef = useRef<any>(null);
  const animationFrameRef = useRef<number | null>(null);

  const target = useRef({
    x: 0,
    y: 0,
    z: 0,
    ry: 0,
  });

  const current = useRef({
    x: 0,
    y: 0,
    z: 0,
    ry: 0,
  });

  function onLoad(spline: any) {
    console.log("Spline loaded:", spline);

    const robot = spline.findObjectByName("RoBOT_(Duplicate)");

    if (!robot) {
      console.error(
        "❌ Robot not found: RoBOT_(Duplicate)"
      );

      return;
    }

    console.log("✅ Robot found:", robot);

    robotRef.current = robot;

    robot.scale.x = 0.75;
    robot.scale.y = 0.75;
    robot.scale.z = 0.75;

    target.current = {
      x: robot.position.x,
      y: robot.position.y,
      z: robot.position.z,
      ry: robot.rotation.y,
    };

    startAnimation();
  }

  function startAnimation() {
    if (animationFrameRef.current) return;

    const animate = () => {
      const robot = robotRef.current;

      if (robot) {
        const c = current.current;
        const t = target.current;

        c.x += (t.x - c.x) * 0.08;
        c.y += (t.y - c.y) * 0.08;
        c.z += (t.z - c.z) * 0.08;
        c.ry += (t.ry - c.ry) * 0.08;

        robot.position.x = c.x;
        robot.position.y = c.y;
        robot.position.z = c.z;

        robot.rotation.y = c.ry;
      }

      animationFrameRef.current =
        requestAnimationFrame(animate);
    };

    animationFrameRef.current =
      requestAnimationFrame(animate);
  }

  useEffect(() => {
    const handleScroll = () => {
      const maxScroll =
        document.documentElement.scrollHeight -
        window.innerHeight;

      if (maxScroll <= 0) return;

      const progress = Math.min(
        Math.max(window.scrollY / maxScroll, 0),
        1
      );

      console.log("Scroll:", progress);

      target.current.x =
        Math.sin(progress * Math.PI * 2) * 250;

      target.current.y =
        Math.sin(progress * Math.PI) * 100;

      target.current.ry =
        Math.sin(progress * Math.PI * 2) * 0.4;
    };

    window.addEventListener(
      "scroll",
      handleScroll,
      { passive: true }
    );

    handleScroll();

    return () => {
      window.removeEventListener(
        "scroll",
        handleScroll
      );

      if (animationFrameRef.current) {
        cancelAnimationFrame(
          animationFrameRef.current
        );
      }
    };
  }, []);

  return (
    <div
      style={{
        position: "fixed",
        right: 0,
        top: 0,
        width: "50vw",
        height: "100vh",
        pointerEvents: "none",
        zIndex: 20,
      }}
    >
      <Spline
        scene="https://prod.spline.design/a6qYqM7f7vcSc179/scene.splinecode"
        onLoad={onLoad}
      />
    </div>
  );
}